# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

"""
This module provides functions for basepair identification.
"""

__name__ = "biotite.structure"
__author__ = "Tom Müller"
__all__ = []

import numpy as np
from .atoms import *
from .superimpose import superimpose, superimpose_apply
from .filter import filter_nucleotides
from .celllist import CellList
from .hbond import hbond
from .error import IncompleteStructureWarning, UnexpectedStructureWarning
from .util import distance, norm_vector

"""
The following functions describe the bases adenine, cytosine, thymine,
guanine and uracil in standard coordinates as described by (Wilma, 2001)
TODO: DOI

They Return:

The bases as list:
    0: AtomArray with nomenclature of PDB File Format V2
    1: AtomArray with nomenclature of PDB File Format V3

The center-coordinates of the aromatic rings as list:
    0: Pyrimidine Ring
    1: Imidazole Ring (if present)

The hydrogen bond donors and acceptors as list
    0: Heteroatoms that are bound to a hydrogen that can act as a donor
    1: Heteroatoms that can act as an acceptor
"""


def  _get_1d_boolean_mask(size, true_ids):
    mask = np.zeros(size, dtype=bool)
    mask[true_ids] = np.ones(len(true_ids), dtype=bool)
    return mask


def _get_std_adenine():
    atom1 = Atom([-2.479, 5.346, 0.000], atom_name="C1*", res_name="A")
    atom2 = Atom([-1.291, 4.498, 0.000], atom_name="N9", res_name="A")
    atom3 = Atom([0.024, 4.897, 0.000], atom_name="C8", res_name="A")
    atom4 = Atom([0.877, 3.902, 0.000], atom_name="N7", res_name="A")
    atom5 = Atom([0.071, 2.771, 0.000], atom_name="C5", res_name="A")
    atom6 = Atom([0.369, 1.398, 0.000], atom_name="C6", res_name="A")
    atom7 = Atom([1.611, 0.909, 0.000], atom_name="N6", res_name="A")
    atom8 = Atom([-0.668, 0.532, 0.000], atom_name="N1", res_name="A")
    atom9 = Atom([-1.912, 1.023, 0.000], atom_name="C2", res_name="A")
    atom10 = Atom([-2.320, 2.290, 0.000], atom_name="N3", res_name="A")
    atom11 = Atom([-1.267, 3.124, 0.000], atom_name="C4", res_name="A")
    adenine_pdbv2 = array(
        [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, 
         atom9, atom10, atom11]
                )
    adenine_pdbv3 = adenine_pdbv2.copy()
    adenine_pdbv3.atom_name[[0]] = ["C1'"]

    # Calculate the coordinates of the aromatic ring centers.
    pyrimidine_center = np.mean(
        [atom5.coord, atom6.coord, atom8.coord, 
         atom9.coord, atom10.coord, atom11.coord], axis=-2
                            )
    imidazole_center = np.mean(
        [atom2.coord, atom3.coord, atom4.coord,
         atom5.coord, atom11.coord], axis=-2
                            )

    # Create boolean masks for the AtomArray containing the bases` 
    # heteroatoms which (or the usually attached hydrogens) can act as
    # Hydrogen Bond Donors or Acceptors respectively.
    hbond_donor_mask = _get_1d_boolean_mask(
        adenine_pdbv2.array_length(), [1, 6]
                                        )
    hbond_acceptor_mask = _get_1d_boolean_mask(
        adenine_pdbv2.array_length(), [1, 3, 6, 7, 9]
                                            )

    return [adenine_pdbv2, adenine_pdbv3], \
           [pyrimidine_center, imidazole_center], \
           [hbond_donor_mask, hbond_acceptor_mask]


def _get_std_cytosine():
    atom1 = Atom([-2.477, 5.402, 0.000], atom_name="C1*", res_name="C")
    atom2 = Atom([-1.285, 4.542, 0.000], atom_name="N1", res_name="C")
    atom3 = Atom([-1.472, 3.158, 0.000], atom_name="C2", res_name="C")
    atom4 = Atom([-2.628, 2.709, 0.000], atom_name="O2", res_name="C")
    atom5 = Atom([-0.391, 2.344, 0.000], atom_name="N3", res_name="C")
    atom6 = Atom([0.837, 2.868, 0.000], atom_name="C4", res_name="C")
    atom7 = Atom([1.875, 2.027, 0.000], atom_name="N4", res_name="C")
    atom8 = Atom([1.056, 4.275, 0.000], atom_name="C5", res_name="C")
    atom9 = Atom([-0.023, 5.068, 0.000], atom_name="C6", res_name="C")
    cytosine_pdbv2 = array(
        [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, atom9]
                    )
    cytosine_pdbv3 = cytosine_pdbv2.copy()
    cytosine_pdbv3.atom_name[[0]] = ["C1'"]

    # Calculate the coordinates of the aromatic ring center.
    pyrimidine_center = np.mean(
        [atom2.coord, atom3.coord, atom5.coord,
         atom6.coord, atom8.coord, atom9.coord], axis=-2
                            )
    
    # Create boolean masks for the AtomArray containing the bases` 
    # heteroatoms which (or the usually attached hydrogens) can act as
    # Hydrogen Bond Donors or Acceptors respectively.
    hbond_donor_mask = _get_1d_boolean_mask(
        cytosine_pdbv2.array_length(), [1, 6]
                                        )
    hbond_acceptor_mask = _get_1d_boolean_mask(
        cytosine_pdbv2.array_length(), [1, 3, 4, 6]
                                            )

    return [cytosine_pdbv2, cytosine_pdbv3], [pyrimidine_center], \
           [hbond_donor_mask, hbond_acceptor_mask]


def _get_std_guanine():
    atom1 = Atom([-2.477, 5.399, 0.000], atom_name="C1*", res_name="G")
    atom2 = Atom([-1.289, 4.551, 0.000], atom_name="N9", res_name="G")
    atom3 = Atom([0.023, 4.962, 0.000], atom_name="C8", res_name="G")
    atom4 = Atom([0.870, 3.969, 0.000], atom_name="N7", res_name="G")
    atom5 = Atom([0.071, 2.833, 0.000], atom_name="C5", res_name="G")
    atom6 = Atom([0.424, 1.460, 0.000], atom_name="C6", res_name="G")
    atom7 = Atom([1.554, 0.955, 0.000], atom_name="O6", res_name="G")
    atom8 = Atom([-0.700, 0.641, 0.000], atom_name="N1", res_name="G")
    atom9 = Atom([-1.999, 1.087, 0.000], atom_name="C2", res_name="G")
    atom10 = Atom([-2.949, 0.139, -0.001], atom_name="N2", res_name="G")
    atom11 = Atom([-2.342, 2.364, 0.001], atom_name="N3", res_name="G")
    atom12 = Atom([-1.265, 3.177, 0.000], atom_name="C4", res_name="G")
    guanine_pdbv2 = array(
        [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, 
         atom9, atom10, atom11, atom12]
                )
    guanine_pdbv3 = guanine_pdbv2.copy()
    guanine_pdbv3.atom_name[[0]] = ["C1'"]

    # Calculate the coordinates of the aromatic ring centers.
    pyrimidine_center = np.mean(
        [atom5.coord, atom6.coord, atom8.coord,
         atom9.coord, atom11.coord, atom12.coord], axis=-2
                            )
    imidazole_center = np.mean(
        [atom2.coord, atom3.coord, atom4.coord,
         atom5.coord, atom12.coord], axis=-2
                            )

    # Create boolean masks for the AtomArray containing the bases` 
    # heteroatoms which (or the usually attached hydrogens) can act as
    # Hydrogen Bond Donors or Acceptors respectively.
    hbond_donor_mask = _get_1d_boolean_mask(
        guanine_pdbv2.array_length(), [1, 7, 9]
                                        )
    hbond_acceptor_mask = _get_1d_boolean_mask(
        guanine_pdbv2.array_length(), [1, 3, 6, 7, 9, 10]
                                            )

    return [guanine_pdbv2, guanine_pdbv3], \
           [pyrimidine_center, imidazole_center], \
           [hbond_donor_mask, hbond_acceptor_mask]


def _get_std_thymine():
    atom1 = Atom([-2.481, 5.354, 0.000], atom_name="C1*", res_name="T")
    atom2 = Atom([-1.284, 4.500, 0.000], atom_name="N1", res_name="T")
    atom3 = Atom([-1.462, 3.135, 0.000], atom_name="C2", res_name="T")
    atom4 = Atom([-2.562, 2.608, 0.000], atom_name="O2", res_name="T")
    atom5 = Atom([-0.298, 2.407, 0.000], atom_name="N3", res_name="T")
    atom6 = Atom([0.994, 2.897, 0.000], atom_name="C4", res_name="T")
    atom7 = Atom([1.944, 2.119, 0.000], atom_name="O4", res_name="T")
    atom8 = Atom([1.106, 4.338, 0.000], atom_name="C5", res_name="T")
    atom9 = Atom([2.466, 4.961, 0.001], atom_name="C5M", res_name="T")
    atom10 = Atom([-0.024, 5.057, 0.000], atom_name="C6", res_name="T")
    thymine_pdbv2 = array(
        [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, atom9, atom10]
                )
    thymine_pdbv3 = thymine_pdbv2.copy()
    thymine_pdbv3.atom_name[[0, 8]] = ["C1'", "C7"]

    # Calculate the coordinates of the aromatic ring center.
    pyrimidine_center = np.mean(
        [atom2.coord, atom3.coord, atom5.coord,
         atom6.coord, atom8.coord, atom10.coord], axis=-2
                            )

    # Create boolean masks for the AtomArray containing the bases` 
    # heteroatoms which (or the usually attached hydrogens) can act as
    # Hydrogen Bond Donors or Acceptors respectively.
    hbond_donor_mask = _get_1d_boolean_mask(
        thymine_pdbv2.array_length(), [1, 4]
                                        )
    hbond_acceptor_mask = _get_1d_boolean_mask(
        thymine_pdbv2.array_length(), [1, 3, 4, 6]
                                            )
      
    return [thymine_pdbv2, thymine_pdbv3], [pyrimidine_center], \
           [hbond_donor_mask, hbond_acceptor_mask]


def _get_std_uracil():
    atom1 = Atom([-2.481, 5.354, 0.000], atom_name="C1*", res_name="U")
    atom2 = Atom([-1.284, 4.500, 0.000], atom_name="N1", res_name="U")
    atom3 = Atom([-1.462, 3.131, 0.000], atom_name="C2", res_name="U")
    atom4 = Atom([-2.563, 2.608, 0.000], atom_name="O2", res_name="U")
    atom5 = Atom([-0.302, 2.397, 0.000], atom_name="N3", res_name="U")
    atom6 = Atom([0.989, 2.884, 0.000], atom_name="C4", res_name="U")
    atom7 = Atom([1.935, 2.094, -0.001], atom_name="O4", res_name="U")
    atom8 = Atom([1.089, 4.311, 0.000], atom_name="C5", res_name="U")
    atom9 = Atom([-0.024, 5.053, 0.000], atom_name="C6", res_name="U")
    uracil_pdbv2 = array(
        [atom1, atom2, atom3, atom4, atom5, atom6, atom7, atom8, atom9]
                )
    uracil_pdbv3 = uracil_pdbv2.copy()
    uracil_pdbv3.atom_name[[0]] = ["C1'"]

    # Calculate the coordinates of the aromatic ring center.
    pyrimidine_center = np.mean(
        [atom2.coord, atom3.coord, atom5.coord,
         atom6.coord, atom8.coord, atom9.coord], axis=-2
                            )

    # Create boolean masks for the AtomArray containing the bases` 
    # heteroatoms which (or the usually attached hydrogens) can act as
    # Hydrogen Bond Donors or Acceptors respectively.
    hbond_donor_mask = _get_1d_boolean_mask(
        uracil_pdbv2.array_length(), [1, 4]
                                        )
    hbond_acceptor_mask = _get_1d_boolean_mask(
        uracil_pdbv2.array_length(), [1, 3, 4, 6]
                                            )

    return [uracil_pdbv2, uracil_pdbv3], [pyrimidine_center], \
           [hbond_donor_mask, hbond_acceptor_mask]


_std_adenine, _std_adenine_ring_centers, \
        _std_adenine_hbond_masks = _get_std_adenine()
_std_cytosine, _std_cytosine_ring_centers, \
        _std_cytosine_hbond_masks = _get_std_cytosine()
_std_guanine, _std_guanine_ring_centers, \
        _std_guanine_hbond_masks = _get_std_guanine()  
_std_thymine, _std_thymine_ring_centers, \
        _std_thymine_hbond_masks = _get_std_thymine()
_std_uracil, _std_uracil_ring_centers, \
        _std_uracil_hbond_masks = _get_std_uracil()

_adenine_containing_nucleotides = ["A", "DA"]
_thymine_containing_nucleotides = ["T", "DT"]
_cytosine_containing_nucleotides = ["C", "DC"]
_guanine_containing_nucleotides = ["G", "DG"]
_uracil_containing_nucleotides = ["U", "DU"]


def get_basepairs(atom_array, min_atoms_per_base = 3):

    basepair_candidates = _get_proximate_basepair_candidates(atom_array)
    basepairs = []

    for basepair_candidate in basepair_candidates:
        base1 = atom_array[_filter_residues(
            atom_array, basepair_candidate[0],basepair_candidate[1]
                                        )
                        ]
        base2 = atom_array[_filter_residues(
            atom_array, basepair_candidate[2], basepair_candidate[3]
                                        )
                        ]

        if _check_dssr_criteria([base1, base2], min_atoms_per_base):
            basepairs.append(basepair_candidate)
    
    return basepairs


def _check_dssr_criteria(basepair, min_atoms_per_base):
    transformed_bases = [None] * 2
    hbond_masks = [None] * 2
    # A list containing one NumPy array for each base with transformed
    # vectors from the standard base reference frame to the structures
    # coordinates. The layout is as follows:
    #
    # [Origin coordinates]
    # [Orthonormal base vectors] * 3 in the order x, y, z
    # [Aromatic Ring Center coordinates]
    transformed_std_vectors = [None] * 2
    contains_hydrogens = np.zeros(2, dtype=bool)

    # Generate the data necessary for analysis for each base.
    for i in range(2):
        base_tuple = _match_base(basepair[i], min_atoms_per_base)
        
        if(base_tuple is None):
            return False
        
        transformed_bases[i], hbond_masks[i], contains_hydrogens[i], \
            transformed_std_vectors[i] = base_tuple

    # Criterion 1: Distance between orgins <= 15 Å
    if not (distance(transformed_std_vectors[0][0,:],
            transformed_std_vectors[1][0,:]) <= 15):
        return False
    
    # Criterion 2: Vertical seperation <= 2.5 Å
    #    
    # Find the intercept between the xy-plane of `transformed_bases[0]`
    # and a line consisting of the origin of `transformed_base[1]` and
    # normal vector (`transformed_std_vectors[0][0,:]` -> z-vector) of
    # `transformed_bases[0]`.
    t = np.linalg.solve(
        np.vstack((transformed_std_vectors[0][1,:],
                   transformed_std_vectors[0][2,:],
                   (-1)*transformed_std_vectors[0][3,:]) 
                ).T,
        (transformed_std_vectors[1][0,:] - transformed_std_vectors[0][0,:])
                    )[0]
    intercept = (transformed_std_vectors[1][0,:]
                + (t * transformed_std_vectors[0][3,:]))
    # The vertical seperation is the distance of the origin of
    # `transformed_bases[1]` and the intercept described above.
    if not (distance(transformed_std_vectors[1][0,:], intercept) <= 2.5):
        return False
      
    # Criterion 3: Angle between normal vectors <= 65°
    if not (np.arccos(np.dot(transformed_std_vectors[0][3,:],
                              transformed_std_vectors[1][3,:])
                    ) >=
            ((115*np.pi)/180)
        ):
        return False
    
    # Criterion 4: Absence of stacking
    if _check_base_stacking(transformed_std_vectors):
        return False
    
    # Criterion 5: Presence of at least on hydrogen bond
    # Check if both bases came with hydrogens.
    if (np.all(contains_hydrogens)):
        # For Structures that contain hydrogens, check for their 
        # presence directly.
        if(len(hbond(transformed_bases[0] + transformed_bases[1],
                     np.ones_like(
                         transformed_bases[0] + transformed_bases[1],
                         dtype=bool
                                ), 
                     np.ones_like(
                         transformed_bases[0] + transformed_bases[1],
                         dtype=bool
                                )
                    )
            ) == 0):
            return False           
    elif not _check_hbonds(transformed_bases, hbond_masks):
        # if the structure does not contain hydrogens, check for
        # plausibility of hydrogen bonds between heteroatoms
        return False

    return True


def _check_hbonds(bases, hbond_masks):
    for donor_base, hbond_donor_mask, acceptor_base, hbond_acceptor_mask in \
        zip(bases, hbond_masks, reversed(bases), reversed(hbond_masks)):
        for donor_atom in donor_base[hbond_donor_mask[0]]:
            for acceptor_atom in acceptor_base[hbond_acceptor_mask[1]]:
                if(distance(acceptor_atom.coord, donor_atom.coord) <= 4.0):
                    return True
    return False


def _check_base_stacking(transformed_vectors):
    # Check for the presence of base stacking corresponding to the
    # criteria of (Gabb, 1996): DOI: 10.1016/0263-7855(95)00086-0

    # Contains the normalized distance vectors between ring centers less
    # than 4.5 Å apart.
    normalized_distance_vectors = []

    # Criterion 1: Distance between aromatic ring centers <= 4.5 Å
    wrongdistance = True
    for ring_center1 in transformed_vectors[0][4:][:]:
        for ring_center2 in transformed_vectors[1][4:][:]:
            if (distance(ring_center1, ring_center2) <= 4.5):
                wrongdistance = False
                normalized_distance_vectors.append(ring_center2 - ring_center1)
                norm_vector(normalized_distance_vectors[-1]) 
    if(wrongdistance == True):
        return False
    
    # Criterion 2: Angle between normal vectors <= 23°
    if not ((np.arccos(np.dot(transformed_vectors[0][3,:],
                              transformed_vectors[1][3,:])))
            <= ((23*np.pi)/180)):
        return False
    
    # Criterion 3: Angle between normalized distance vector and one 
    # normal vector <= 40°
    for vector in transformed_vectors:
        for normalized_dist_vector in normalized_distance_vectors:    
            if (np.arccos(np.dot(vector[3,:], normalized_dist_vector))
                <= ((40*np.pi)/180)):
                return True
    
    return False


def _match_base(base, min_atoms_per_base):
    # Matches a nucleotide to a standard base
    # Returns: 
    # ret_base : The base or if the base atoms are incomplete a
    #               superimposed standard base
    # ret_hpos : A list of size 2 containing boolean masks. 
    #               Pos 0 contains the het_atoms that act as H-Donors
    #               Pos 1 contains the het_atoms that act as H-Acceptors
    # contains_hydrogens : A boolean; if True the base contains H-Atoms
    # vectors : A set of std_vectors (Origin, Orthonormal-Base-Vectors, 
    #               Ring-Centers) transformed onto the
    #               nucleotides coordinates   

    return_hbond_masks = [None] * 2
    contains_hydrogens = False

    vectors = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0],
                             [0, 0, 1]], np.float)

    # Check base type and match standard base.
    if(base[0].res_name in _adenine_containing_nucleotides):
        std_base = _std_adenine
        std_ring_centers = _std_adenine_ring_centers
        std_hbond_masks = _std_adenine_hbond_masks
    elif(base[0].res_name in _thymine_containing_nucleotides):
        std_base = _std_thymine
        std_ring_centers = _std_thymine_ring_centers
        std_hbond_masks = _std_thymine_hbond_masks
    elif(base[0].res_name in _cytosine_containing_nucleotides):
        std_base = _std_cytosine
        std_ring_centers = _std_cytosine_ring_centers
        std_hbond_masks = _std_cytosine_hbond_masks
    elif(base[0].res_name in _guanine_containing_nucleotides):
        std_base = _std_guanine
        std_ring_centers = _std_guanine_ring_centers
        std_hbond_masks = _std_guanine_hbond_masks
    elif(base[0].res_name in _uracil_containing_nucleotides):
        std_base = _std_uracil
        std_ring_centers = _std_uracil_ring_centers
        std_hbond_masks = _std_uracil_hbond_masks 
    else:
        raise UnexpectedStructureWarning("Base Type not supported. Unable to "
                                         "check for basepair")
        return None

    # Check if the structure uses PDBv3 or PDBv2 atom nomenclature.
    if (np.sum(np.in1d(std_base[1].atom_name, base.atom_name))
        > np.sum(np.in1d(std_base[0].atom_name, base.atom_name))):
        std_base = std_base[1]
    else:
        std_base = std_base[0]

    # Add the ring centers to the array of vectors to be transformed.
    vectors = np.vstack((vectors, std_ring_centers))
    
    # Match the selected std_base to the base.
    fitted, transformation = superimpose(
                        base[np.in1d(base.atom_name, std_base.atom_name)],
                        std_base[np.in1d(std_base.atom_name, base.atom_name)]
                                        )
    # Transform the vectors
    trans1, rot, trans2 = transformation
    vectors += trans1
    vectors  = np.dot(rot, vectors.T).T
    vectors += trans2   
    # Normalize the transformed orthogonal base vectors   
    for i in range(1, 4):
        vectors[i,:] = vectors[i,:]-vectors[0,:]
        norm_vector(vectors[i,:])

    # Investigate the completeness of the base:
    # 
    # A length difference of zero means the base contains all atoms of
    # the std_base          
    length_difference = len(std_base) - len(fitted) 
    if(length_difference > 0 and len(fitted) >= min_atoms_per_base):
        # If the base is incomplete but contains 3 or more atoms of the 
        # std_base, transform the complete std_base and use it to
        # approximate the base.
        raise IncompleteStructureWarning("Base is not complete. Attempting "
                                            "to emulate with std_base.")
        return_base = superimpose_apply(std_base, transformation)
        return_hbond_masks = std_hbond_masks
        contains_hydrogens = False
    elif (length_difference > 0):
        # If the base is incomplete and contains less than 3 atoms of 
        # the std_base throw warning
        raise IncompleteStructureWarning("Base is smaller than 3 atoms. "
                                            "Unable to check for basepair.")
        return None
    else:
        # If the base is complete use the base for further calculations.
        #
        # Generate a boolean mask containing only the base atoms, 
        # disregarding the sugar atoms and the phosphate backbone.
        base_atom_mask = np.ones(len(base), dtype=bool)
        for i in range(len(base)):
            if((base[i].atom_name not in std_base.atom_name) and
               (base[i].element != "H")):
                base_atom_mask[i] = False
        
        # Create boolean masks for the AtomArray containing the bases` 
        # heteroatoms, which (or the usually attached hydrogens) can act 
        # as Hydrogen Bond Donors or Acceptors respectively, using the
        # std_base as a template.
        for i in range(2):
            return_hbond_masks[i] = _filter_atom_type(base[base_atom_mask], 
                                std_base[std_hbond_masks[i]].atom_name)

        # Check if the base contains Hydrogens.
        if ("H" in base.element[base_atom_mask]):
            contains_hydrogens = True
            return_base = base[base_atom_mask]          
        else:
            return_base = base[base_atom_mask]
        
    return return_base, return_hbond_masks, contains_hydrogens, vectors


def _get_proximate_basepair_candidates(atom_array, max_cutoff = 15,
                                       min_cutoff = 9):
    # gets proximate basepairs, where the C1-Sugar-Atoms are within
    # `min_cutoff<=x<=max_cutoff`
    c1sugars = atom_array[filter_nucleotides(atom_array) 
                     & _filter_atom_type(atom_array, ["C1'", "C1*"])]
    adjacency_matrix = CellList(
        c1sugars, max_cutoff
                            ).create_adjacency_matrix(max_cutoff)
    
    basepair_candidates = []
    for ix, iy in np.ndindex(adjacency_matrix.shape):
        if (adjacency_matrix[ix][iy]):
            candidate = [c1sugars[ix].res_id, c1sugars[ix].chain_id]
            partner = [c1sugars[iy].res_id, c1sugars[iy].chain_id]
            if ((distance(c1sugars[ix].coord, c1sugars[iy].coord) > min_cutoff) 
                 & ((partner + candidate) not in basepair_candidates)):
                basepair_candidates.append(candidate + partner)
    
    return basepair_candidates


def _filter_atom_type(atom_array, atom_names):
    # Filter all atoms having the desired `atom_name`.
    return (
        np.isin(atom_array.atom_name, atom_names)
        & (atom_array.res_id != -1)
        )


def _filter_residues(atom_array, res_ids, chain_id = None):
    # Filter all atoms having the desired 'residue_id' and 'chain_id'
    if chain_id is None:
        chain_mask =  np.ones(atom_array.array_length(), dtype=bool)
    else:
        chain_mask = np.isin(atom_array.chain_id, chain_id)

    return np.isin(atom_array.res_id, res_ids) & chain_mask
        
